Product Changelog
=================

Roadmap
-------

 TBD

1.0 Release
-----------
1.0.8
^^^^^

* Support for python 3.7

1.0.7
^^^^^

 * Fix: Traceback shown when status report called with no records

1.0.6
^^^^^

 * Fix: Timezone offset double-applied in views
 * Fix: Tomer edit parameter --make-running renamed --make-active
 * New: Provide user feedback while running commands

1.0.5
^^^^^

 * Fix: Tracebacks when starting non-existing task
 * New: Resume previous task
 * Enhancement: Major refactoring of CLI table logic

1.0.4
^^^^^

 * New: Additional shortcut parameters for summary and reporting views
 * New: Support for editing timer records
 * New: Support for deleting timer records

1.0.3
^^^^^
 
 * Fix: Timezone issue while grouping records in reporting views
 * Fix: CLI should always refer to times in local timezone
 * Enancement: Major build system refactoring

1.0.2
^^^^^

 * Fix: Week ranges sometimes produced wrong week for edge cases.
 * New: Show total in summary view
 * New: Status command

1.0.1
^^^^^

 * Fix: Column formatting across weeks in report view
 * Fix: Default timespan for "records" view should be current day
 * Fix: Default timespan for "summary" view should be current day
 * New: Fancy grid now default style for tables
 * New: Add `--version` command line switch

1.0.0
^^^^^

 * First public release
