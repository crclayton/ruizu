for dir in "$@"; do
  for f in "$dir"/*.mp3; do
    [ -e "$f" ] || continue

    d=${f%/*}
    n=${f##*/}
    name=${n%.*}
    ext=${n##*.}

    b=$(printf '%s\n' "$name" \
        | sed -E 's/^[0-9]+([._-][0-9]+)?[._-]+//' \
        | tr -d '.')

    new="$b.$ext"
    [ "$new" != "$n" ] && mv -f -- "$f" "$d/$new"
  done
done
