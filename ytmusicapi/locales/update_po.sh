#!/usr/bin/env bash
for dir in *
do
  if (( ${#dir} >=2 && ${#dir} <=5 ));
  then
    msgmerge --update ${dir}/LC_MESSAGES/base.po base.pot --no-fuzzy-matching
  fi
done