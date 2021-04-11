#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr  5 13:12:34 2021

@author: jeffrocks
"""

#imports for fully decoded version
#from binascii import hexlify, unhexlify

#imports for runtime

import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np
import sys
import time
import copy
import struct
import subprocess
from os import walk


#UTXO class
class UTXO:
    
    def __init__(self, h, a):
        self.height = h
        self.amount = a
    
    

#decode the binary best block hash (256 bit = 32 bytes)
def decode_hex256(bbhash_b):

    #make sure byte length is 32    
    assert(len(bbhash_b)==32)

    # call in as 8 uints then convert to 1 hex string   
    bbhash = ''
    a = struct.unpack('>8I', bbhash_b[::-1])
    for ai in a:
        bbhash += '{0:08x}'.format(ai)
        
    return bbhash


#parse the varint
#code modified from https://github.com/sr-gi/bitcoin_tools/blob/0f6ea45b6368200e481982982822f0416e0c438d/bitcoin_tools/analysis/status/utils.py
def parse_b128(fin):
    data = fin.read(1).hex()
    more_bytes = int(data, 16) & 0x80
    while more_bytes:
        tmp = fin.read(1).hex()
        data += tmp
        more_bytes = int(tmp, 16) & 0x80

    return data


#decode the varint
#code modified from https://github.com/sr-gi/bitcoin_tools/blob/0f6ea45b6368200e481982982822f0416e0c438d/bitcoin_tools/analysis/status/utils.py
def b128_decode(data):
    n = 0
    i = 0
    while True:
        d = int(data[2 * i:2 * i + 2], 16)
        n = n << 7 | d & 0x7F
        if d & 0x80:
            n += 1
            i += 1
        else:
            return n


#decompress a bitcoin amount
#code modified from https://github.com/sr-gi/bitcoin_tools/blob/0f6ea45b6368200e481982982822f0416e0c438d/bitcoin_tools/analysis/status/utils.py
def txout_decompress(x):
    if x == 0:
        return 0
    x -= 1
    e = x % 10
    x = x // 10
    if e < 9:
        d = (x % 9) + 1
        x = x // 9
        n = x * 10 + d
    else:
        n = x + 1
    while e > 0:
        n *= 10
        e -= 1
    return n

#parse the script portion of the utxo
def parse_script(data_b, data_size, first_byte):
    
    data = data_b.hex()
    if first_byte:
        data = first_byte+data
    return data
        
    #to decompress script in future look at
    #modified from https://github.com/sr-gi/bitcoin_tools/blob/0f6ea45b6368200e481982982822f0416e0c438d/bitcoin_tools/analysis/status/utils.py#L259


# read the utxo dump file header
def read_fileheader(fin):
    #get binary base block_hash, coin count, and ? from header info
    bbhash_b = fin.read(32)
    ccount_b = fin.read(8)
    txcount_b = fin.read(4)
    
    #decode binary bbhash, ccount
    bbhash = decode_hex256(bbhash_b)
    ccount = struct.unpack('Q', ccount_b)[0]
    txcount = struct.unpack('I', txcount_b)[0]
        
    return ccount


#read a single UTXO
def get_UTXO(fin):
    
    ### Read in bytes of utxo
    
    #read in txid, outnum
    txid_b = fin.read(32)
    outnum_b = fin.read(4)
    
    #read the binary stream until stop given by Varint
    code = parse_b128(fin)
    
    #next varint is the utxo amount
    amount_v = parse_b128(fin)
    
    #next varint is the script type
    out_type_v = parse_b128(fin)
    
    #script type must be decoded now because it has variable length
    out_type = b128_decode(out_type_v)
    
    #get data size based on script type
    NSPECIALSCRIPTS = 6
    first_byte = None
    if out_type in [0, 1]:
        data_size = 20  # 20 bytes
    elif out_type in [2, 3, 4, 5]:
        data_size = 32  
        first_byte = out_type_v[-1] # need previous byte from stream
    else:
        data_size = (out_type - NSPECIALSCRIPTS) * 1
    
    #parse script
    script_b = fin.read(data_size)
    
    

    # ### decode txid, outnum, heigh, coinbase and btc amount
    
    #decode txid, outnum
    #txid = decode_hex256(txid_b)
    #outnum = struct.unpack('I', outnum_b)[0]
        
    # #decode the varint to get coinbase and height
    code = b128_decode(code)
    height = code >> 1
    #coinbase = code & 0x01
    
    # #decode btc amount of utxo
    amount = txout_decompress(b128_decode(amount_v))
    
    utxo = UTXO(height,amount)
    
    return utxo
    
    #decode script
    #script = parse_script(script_b, data_size, first_byte)    


#read a batch of utxos
def get_UTXOs(fin, batch_size):
    
    #read in batch of utxos
    utxos = []
    for u in range(batch_size):
        utxos.append(get_UTXO(fin))   
    
    return utxos

#generate histogram of a batch of utxos
def get_Histogram(utxos, xedges, yedges):
    
    #place batch into histogram
    x = [utxo.height for utxo in utxos]
    y = [utxo.amount for utxo in utxos]
    x = np.array(x)
    y = np.array(y)*1e-8
    
    #take log of amounts
    y[np.where(y==0)]=1e-9
    y = np.log10(y)
    
    tmp_hist, xedges, yedges = np.histogram2d(x, y, (xedges, yedges))
    return tmp_hist, xedges, yedges


#ask user to select file name if multiple
def get_filename():
    
    #get file list of directory
    _, _, filenames = next(walk('.'))
    dat_files = [f for f in filenames if '.dat' in f]
    
    #check for zero dat files
    if not dat_files:
        print('\nError, no utxo.dat files found in this directory. \
Make sure the utxo dump file from core is in this directory')
        sys.exit()
    
    #if only one dat file, then use that one, o.w. ask which
    utxo_fn = './'+dat_files[0]
    if len(dat_files)>1:
        print('\nVisualize which utxo file ?\n')
        for n in range(len(dat_files)):
            print(str(n+1)+") "+dat_files[n])
        try:
            fnum = int(input("Enter a number: "))
            utxo_fn = './'+dat_files[fnum-1]
        except:
            print('\nError, could not open file. Type the right number?')
            sys.exit()
    
    #check for incomplete
    if 'incomplete' in utxo_fn:
        print('\nError, core has not finished dumping the file')
        sys.exit()
    
    #get block height from file name
    block_height = 0
    try:
        block_height = int(utxo_fn[2:-4])
    except:
        print('\nError: the file name is not a valid block height')
        sys.exit()
    
    #check reasonable block+heights
    if block_height < 600000 or block_height > 6000000:  #100 years from now
        print('\nError: the file name is not a valid block height')
        sys.exit()
        
    return utxo_fn, block_height

# %%
    
def openImage(path):
    imageViewerFromCommandLine = {'linux':'xdg-open',
                                  'win32':'explorer',
                                  'darwin':'open'}[sys.platform]
    subprocess.run([imageViewerFromCommandLine, path])


# %%

###  MAIN #####

start_time = time.time()    


utxo_fn, block_height = get_filename()

#get buffered reader to utxo file
fin = open(utxo_fn,'rb')


#set histogram resolution
max_yedge = 5
min_yedge = -8
yres = 800
xres = yres*2
maxx = block_height+3     #adding three for padding here
minx = 1
yedges = np.linspace(-8, max_yedge, yres-3)
yedges = np.concatenate(([-10,-9,-8.5], yedges, [10]))
xedges = np.linspace(minx, maxx, xres+1)
hist = np.zeros(shape=(xres,yres), dtype=float)


#read utxo file header
coin_count = 0
try:
    coin_count = read_fileheader(fin)
except:
    print('\nError reading file header')
    sys.exit()

print("\nRendering the "+str(coin_count)+" utxos in "+utxo_fn[2:]+"...\n")

print("This should take between 10 and 30 min...\n")

#size of batch of utxos to call in
batch_size = coin_count // 100



#start processing batches of coins
coins_processed = 0
while coins_processed < coin_count:
    
    #check for the size of the final batch call
    coins_remaining = coin_count-coins_processed
    if coins_remaining < batch_size:
        batch_size = coins_remaining
    
    #get batch of utxos
    utxos = get_UTXOs(fin, batch_size)
    
    #get histogram
    tmp_hist,xedges,yedges = get_Histogram(utxos, xedges, yedges)
    hist += tmp_hist
    
    #update user on status
    coins_processed += batch_size
    perc_done = (100*coins_processed) // coin_count
    print("Percent completed: "+str(perc_done)+"%")

print("\nRendering and saving image...")


# %% format the hist matrix for rendering

#phist = np.copy(hist)
phist = hist

#non-zero, take logs and rotate hist matrix
phist[np.where(phist==0)]=.01
phist = np.log10(phist)
phist = np.rot90(phist)
phist = np.flipud(phist)

# get max values
hmax = phist.max()
hmin = phist.min()

# insert nan from zero value bins
phist[np.where(phist==hmin)]=np.nan

# adjust the one sat and zero sat position so easier to see in plot
phist[10,:] = phist[1,:]
phist[6,:] = phist[0,:]


# %%


# get figure handles
plt.clf()
fig = plt.figure(figsize=(8, 6), facecolor='black')
ax = fig.add_axes([.11,.37,.8,.55])

#color maps for pcolor
my_cmap = copy.copy(cm.gnuplot2)
my_cmap.set_bad(color='black')

# render scatter
im = ax.pcolormesh(phist, vmin=-1, vmax=np.floor(hmax*.6), cmap=my_cmap, label='UTXO Histogram')

#yaxis format
plt.yticks(np.linspace(0, yres, num=14))
labels = ["100k","10k","1k",'100','10',
              "1",".1",'.01','.001','10k sat',
              "1k sat","100 sat",'10 sat','0 sat',] 
labels.reverse()
ax.set_yticklabels(labels, fontsize=8)
ax.yaxis.set_ticks_position('both')
ax.tick_params(labelright=True)


#xaxis format
ticks_year=['2009','2010','2011','2012',
            '2013','2014','2015','2016',
            '2017','2018','2019','2020','2021']
ticks_height = [1,32500,100400,160400,
                214500,278200,336700,391300,
                446200,502100,556500,610800,664100]
ticks_x = []
label_x = []
for n in range(len(ticks_height)):
    th = ticks_height[n]
    ticks_x.append(np.argmin(np.abs(np.array(xedges)-th)))
    label_x.append(ticks_year[n]+"\n"+str(th))
    
plt.xticks(ticks_x)
ax.set_xticklabels(label_x, rotation=0, fontsize=6)


#title and labels
tick_color = "white"
fig_title = "  The Bitcoin Blockchain (from file "+utxo_fn[2:]+")"
tobj = plt.title(fig_title, fontsize=12, loc='left')
plt.setp(tobj, color=tick_color)
ax.set_ylabel('Amount (BTC)', fontsize=8)
ax.spines['bottom'].set_color(tick_color)
ax.spines['top'].set_color(tick_color)
ax.tick_params(axis='x', colors=tick_color)
ax.xaxis.label.set_color(tick_color)
ax.spines['right'].set_color(tick_color)
ax.spines['left'].set_color(tick_color)
ax.tick_params(axis='y', colors=tick_color)
ax.yaxis.label.set_color(tick_color)
ax.set_xlabel("Output time (year, block height)", fontsize=8)


#  Color bar
cbaxes = fig.add_axes([0.75, .925, 0.2, 0.015]) 
cb = plt.colorbar(im, orientation="horizontal", cax=cbaxes)
cbaxes.set_xlim(-0.01,np.floor(hmax*.8)+.1)
cbaxes.xaxis.set_ticks_position('top')
cbticks = np.arange(int(np.floor(hmax*.6))+1)
cb.set_ticks(cbticks)
clabels = ['1','10','100','1k','10k','100k','1M'] 
cbaxes.set_xticklabels(clabels[0:len(cbticks)], fontsize=6)
cbaxes.set_ylabel("Number of \nunspent outputs", rotation=0, fontsize=6)
cbaxes.yaxis.set_label_coords(-.25,0)
cbaxes.tick_params('both', length=0, width=0, which='major')
cb.outline.set_visible(False)
cbaxes.spines['bottom'].set_color(tick_color)
cbaxes.tick_params(axis='x', colors=tick_color)
cbaxes.yaxis.label.set_color(tick_color)


# save the image
fig_name = "./utxo_heatmap_"+str(block_height)+".png"
plt.savefig(fig_name, dpi=1200, bbox_inches='tight', facecolor=fig.get_facecolor(), transparent=True)
print("\nImage saved as "+fig_name)
print("\nDone")

# try to open the image automatically
try:
    openImage(fig_name)
except:
    sys.exit()


# %%
    
    
#print("\nrun time: ", time.time() - start_time)

