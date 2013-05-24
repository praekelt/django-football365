Changelog
=========

0.2
---
#. Make `football365_fetch` command more robust by looking up XML nodes by tag name.
#. Add tests. Check that feeds are being parsed correctly, and fields are populated with valid data.

0.1.3
-----
#. Add timeout for `urlopen` in `football365_fetch` command. The prevents accumulation of long-running transactions.

0.1.2
-----
#. Allow url to be overridden per call.

0.1.1
-----
#. Escape special XML characters. Teamtalk feeds aren't correctly escaped.

0.1
---
#. Convert to south.
#. Allow client account id to be overridden per call. Needed because Teamtalk changed the rules.

0.0.3
-----
#. Handle XML feed change.

0.0.2
-----
#. Change default ordering.

0.0.1
-----
#. Initial release.

