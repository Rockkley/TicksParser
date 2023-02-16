# TicksParser BETA v 0.5
![preview](https://github.com/Rockkley/TicksParser/blob/master/tpgp.png)

Software to parse and save stock ticks using official Metatrader 5 API

Supported formats for saving ticks: pkl, csv, json, html, xml, xlsx

***work in progress***

## Known issues:
- [ ] Parsing all symbol's ticks for the whole period at once, what leads to fail on parsing big amount of ticks (unknown amount).
- [ ] Blocks main thread during parsing ticks
- [ ] Fails to create treeview of symbols found on server with multiple sub-dirs.
- [ ] Logger window is not used.
- [ ] The parsed ticks aren't stored temporary anywhere, what may lead to re-parsing ticks that have been already 
parsed before just to save it in a different format.
- [ ] Login information hardcoded
- [ ] It's possible to set date_to < date from
- [ ] Only pandas.to_ formats are available
- [ ] GUI code is not properly structured 
- [ ] Minimalistic GUI
- [ ] Missing option to add accounts via GUI
- [ ] Missing option to set hours and minutes in dates 
- [ ] Missing compressing options for saving ticks
- [ ] Missing documentation for some classes and functions.
- [ ] Assorti of code smells
