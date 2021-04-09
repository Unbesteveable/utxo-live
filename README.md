<!-- ABOUT THE PROJECT -->
## UTXO-LIVE

<br>

This python script generates a heatmap visualization of the blockchain stored on your local Bitcoin node. 

<br>

<img src="https://utxo.live/utxo_heatmap_678336.png" alt="Logo" >


<br>


## Overview

Every Bitcoin node accounts for all coins at all times by actively managing its UTXO (Unspent Transaction Output) database.  This project renders a heatmap of the UTXO database that shows all coins in a single image (as seen on <a href=https://utxo.live/>utxo.live</a>). The heatmap is a two dimensional histogram arranged by the date and BTC amount of each output.

<!-- Requirements -->
## Requirements
* Bitcoin Core version 0.20 or higher
* Python3 (you already have it)


## Instruction summary
* Create a folder `utxo-live` in a familiar place on your machine
* Dump the utxo set `dumptxoutset` to a file `xxxxxx.dat` where xxxxxxx is the block height (5 min) 
* Download and run `utxo-live.py` on the dump file (20 min)

## Steps

1. Create a new folder called `utxo-live` in a familiar location on your machine (e.g. in your Documents folder).

2. Open a terminal window and display the current directory

  * On Windows open a terminal with Start -> Command Prompt and then type 
  ```sh
  >> echo %cd%
  ```
  
  * On Mac open  Applications -> Utilities -> Terminal and type
  ```sh
  >> pwd
  ```
  
  ```sh
  You already know
  ``` Linux

2. Open the console interface on Bitcoin Core


