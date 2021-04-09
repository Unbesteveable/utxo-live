<!-- ABOUT THE PROJECT -->
## UTXO-LIVE

<br>

This project generates a heatmap visualization of the Bitcoin blockchain stored on your local node. 

<br>

<img src="https://utxo.live/utxo_heatmap_678336.png" alt="Logo" >


<br>


## Overview

Every Bitcoin node accounts for all coins at all times by actively managing its UTXO (Unspent Transaction Output) database.  The python script above renders a heatmap of the UTXO database that shows all coins in a single image (as seen on <a href=https://utxo.live/>utxo.live</a>). The heatmap is a two dimensional histogram arranged by the date and BTC amount of each output.

<!-- Requirements -->
## Requirements
* Bitcoin Core version 0.20 or higher
* Python3 (you already have it)


## Instruction summary for experienced users
* Create a folder `utxo-live` in a familiar place on your machine
* Dump the utxo set `dumptxoutset` to a file `<path to utxo-live>/xxxxxx.dat` where xxxxxxx is your nodes current block height (5 min) 
* Download and run `utxo-live.py` on the dump file (20 min)

## Step by step instructions
1. Make sure Bitcoin Core is running and synchronized.

2. Create a new folder called `utxo-live` in a familiar location on your machine (e.g. in your Documents folder).

3. Open a terminal window and display the current folder.

  * Windows: open a terminal (Start -> Command Prompt) and type: 
  ```sh
  echo %cd%
  ```
  
  * Mac/Linux: open a terminal (Mac: Applications -> Utilities -> Terminal) and type:
  ```sh
  pwd
  ```
  
4. Navigate to the `utxo-live` folder using the change directory `cd` command. For example if you're currently in `Documents` and you've created the folder  `Documents/bitcoin-tools/utxo-live/` then type: 

  ```sh
  cd bitcoin-tools/utxo-live/
  ```
  Note: Windows sometimes requires forward slashes `/` instead of back slashes `\`.
  
5. Again display the full folder path (Step 3) and copy the path to your clipboard. We will be pasting this path into Bitcoin Core soon.

6. Leave the terminal window there, and open the Bitcoin Core console window. (Alternatively for bitcoin-cli users, open another terminal window and type the console commands in the next steps as `bitcoin-cli` commands.)

<img src="https://miro.medium.com/max/1098/1*DEukIfd6csdA6bbl2K5sSg.jpeg" alt="Open Console Pic" >

7. Get the current block height by typing in the console window:

  ```sh
  getblockcount
  ```
  and hitting enter.

8. Dump the current utxo set by typing in the console window:

```sh
  dumptxoutset <PATH to utxo-live>/<xxxxxx.dat>
  ```
  where `<PATH to utxo-live>` is copy-pasted from Step 5, and `<xxxxxx.dat>` is the block height. For example if the block height was 654321, the command will look something like:

```sh
  dumptxoutset /Users/Steve/Documents/bitcoin-tools/utxo-live/654321.dat
  ```
  Hit enter. If there are no error messages then it's working. It will take 5-10 minutes. Look in your `utxo-live` folder and you should see the file being created as `xxxxxx.dat.incomplete`


