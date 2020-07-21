#!/usr/bin/env bash
for dir in *
do
  if [ ${#dir} -eq 2 ];
  then
    msgfmt -o ${dir}/LC_MESSAGES/base.mo ${dir}/LC_MESSAGES/base
  fi
done