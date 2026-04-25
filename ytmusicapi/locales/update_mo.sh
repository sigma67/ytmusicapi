#!/usr/bin/env bash
for dir in *
do
  if (( ${#dir} >=2 && ${#dir} <=5 ));
  then
    msgfmt -o ${dir}/LC_MESSAGES/base.mo ${dir}/LC_MESSAGES/base
  fi
done