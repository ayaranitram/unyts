# unyts
After culminated a project for a class from MITx couses, I saw the opportunity to use a *dgraph network* to built a unit converter able to from any units to any units without the need to populate a huge but finite table of possible conversions. Powered by BFS algorith to search through the network, this converter is able to found conversions from a particular unit (or ratio of units) to any other unit (or ratio) as long as a path connecting them exists.

This package is under development and is regularly updated. Backcompatibility is intented to be maintained when possible.

## What Contains This Package
- It is loaded with the network of untis preloaded for distances, area, volume, mass and time conversions defined for SI and Imperial systems according to the definition of each unit, i.e.: _1_foot = 12_inches_.
- Prefixes applied to the basic units, like _k_ to _m_ to make _km_, are loaded as a network of conversions paths allowing the algorith to apply the prefix to any other unit on the same system.
- It provides classes of _units_ useful powered with arithmetich and logic operations to intrincically consider unit conversions when making calculations.

## To install this package:
pip install unyts