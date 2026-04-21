cd ~/Music/library/genres
find . -type f -print0 | while IFS= read -r -d '' f; do
  dir=$(dirname "$f")
  base=$(basename "$f")
  new=$(echo "$base" | perl -pe 's/\.(?=.*\.)//g')
  if [[ "$base" != "$new" ]]; then
    echo mv -- "$f" "$dir/$new"
    mv "$f" "$dir/$new"
  fi
done

declare -A counts
find . -type f | while read -r file; do
    dir=$(dirname "$file")
    base=$(basename "$file")
    filename="${base%.*}"
    extension="${base##*.}"

    # If the file has no extension, handle it gracefully
    if [[ "$filename" == "$extension" ]]; then
        extension=""
    else
        extension=".$extension"
    fi

    # Check if we've seen this filename before
    if [[ -n "${counts[$base]}" ]]; then
        ((counts[$base]++))
        new_name="${filename}_$(printf "%02d" "${counts[$base]}")$extension"
        echo $file "$dir/$new_name"
        mv -n "$file" "$dir/$new_name"
    else
        counts[$base]=0
    fi
done
