for dir in "$@"; do
  for f in "$dir"/*.mp3; do
    [ -e "$f" ] || continue

    d=${f%/*}
    n=${f##*/}
    name=${n%.*}
    ext=${n##*.}

    # skip files already prefixed with a YYYYMMDD timestamp
    [[ "$name" =~ ^[0-9]{8}- ]] && continue

    b=$(printf '%s\n' "$name" \
        | sed -E 's/^[0-9]+([._-][0-9]+)?[._-]+//' \
        | tr -d '.')

    birth=$(stat --format='%W' "$f")
    if [[ "$birth" -gt 0 ]]; then
      ts=$(date -d "@$birth" +%Y%m%d)
    else
      ts=$(date -r "$f" +%Y%m%d)
    fi
    new="${ts}-${b}.${ext}"
    [ "$new" != "$n" ] && mv -f -- "$f" "$d/$new"
  done
done
