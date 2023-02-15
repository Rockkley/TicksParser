# TicksParser BETA v 0.5


Software to parse and save stock ticks using official Metatrader 5 API

Supported formats for saving: pkl, csv, json, html, xml, xlsx

***work in progress***

## Known issues:
- [ ] Parsing all symbol's ticks for whole period at once, what leads to failing parse big amount of ticks (unknown amount).
- [ ] Fails to create treeview of symbols found on server with multiple sub-dirs.
- [ ] Logger window is not used.
- [ ] The parsed ticks aren't stored temporary anywhere, what may lead to re-parsing ticks that has been already 
parsed before just to save it in a different format.
- [ ] Login information hardcoded
- [ ] It's possible to set date_to < date from
- [ ] Only pandas.to_ formats are available
- [ ] Missing option to add accounts via gui
- [ ] Missing option to set hours and minutes in dates 
- [ ] Missing compressing options for saving ticks
- [ ] Missing documentation for some classes and functions.
- [ ] Assorti of code smells
