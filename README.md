<!-- ABOUT THE PROJECT -->
## UTXO-LIVE

This python script generates a heatmap visualization of the blockchain stored on your local bitcoin node. 

## Overview

Every bitcoin node accounts for all coins at all times by actively managing its UTXO (Unspent Transaction Output) database.  This project renders a heatmap of the UTXO database that shows all coins in a single image (as seen on <a href=https://utxo.live/>utxo.live</a>). The heatmap is a two dimensional histogram arranged by the date and bitcoin amount of each output.

<!-- Requirements -->
## Requirements
* Bitcoin Core version 0.20 or higher
* Python3 (you already have it)


## Instructions summary
* Create a folder `utxo-live` in a familiar place on your machine
* Dump the utxo set `dumptxoutset` to a file `xxxxxx.dat` where xxxxxxx is the block height (5 min) 
* Download and run `utxo-live.py` on the dump file (20 min)

## Instructions summary

