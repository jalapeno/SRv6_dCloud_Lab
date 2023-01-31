## SRv6 localsids

1. Deploy the srv6-localsids-processor
```
cd ~/SRv6_dCloud_Lab/lab_8/python/
python3 srv6-localsids-processor.py
```
Expected output:
```
document added:  xrd01_fc00:0:1111::
document added:  xrd01_fc00:0:1111:e000::
document added:  xrd01_fc00:0:1111:e001::
document added:  xrd01_fc00:0:1111:e002::
document added:  xrd01_fc00:0:1111:e003::
document added:  xrd01_fc00:0:1111:e004::
document added:  xrd01_fc00:0:1111:e005::
document added:  xrd01_fc00:0:1111:e006::
document added:  xrd01_fc00:0:1111:e007::
document added:  xrd01_fc00:0:1111:e008::
document added:  xrd01_fc00:0:1111:e009::
document added:  xrd07_fc00:0:7777::
document added:  xrd07_fc00:0:7777:e000::
document added:  xrd07_fc00:0:7777:e001::
document added:  xrd07_fc00:0:7777:e002::
document added:  xrd07_fc00:0:7777:e003::
document added:  xrd07_fc00:0:7777:e004::
document added:  xrd07_fc00:0:7777:e005::
document added:  xrd07_fc00:0:7777:e006::
document added:  xrd07_fc00:0:7777:e007::
```
1. Check that Arango as an *`srv6_local_sids`* data collection, and that it is populated
2. you can now kill the processor with ctrl-c. It'll kick out python errors, but no worries...

