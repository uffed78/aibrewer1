def filter_styles(
    beer_styles,
    category=None,
    abv_min=0, abv_max=100,
    ibu_min=0, ibu_max=1000,
    srm_min=0, srm_max=100,
    og_min=0, og_max=2,
    fg_min=0, fg_max=2
):
    """
    Filtrerar ölstilar baserat på attribut som kategori, ABV, IBU, SRM, OG, FG.
    """
    filtered = []
    for style in beer_styles:
        try:
            # Hämta numeriska värden och konvertera till float
            abv_low = float(style.get("abvmin", 0))
            abv_high = float(style.get("abvmax", 100))
            ibu_low = float(style.get("ibumin", 0))
            ibu_high = float(style.get("ibumax", 1000))
            srm_low = float(style.get("srmmin", 0))
            srm_high = float(style.get("srmmax", 100))
            og_low = float(style.get("ogmin", 0))
            og_high = float(style.get("ogmax", 2))
            fg_low = float(style.get("fgmin", 0))
            fg_high = float(style.get("fgmax", 2))
        except ValueError:
            print(f"Varning: Ogiltigt numeriskt värde i stil: {style['name']}")
            continue

        # Filtrera på kategori (om angivet)
        if category and category.lower() not in style.get("category", "").lower():
            continue

        # Kontrollera numeriska filter
        if not (
            abv_low >= abv_min and abv_high <= abv_max and
            ibu_low >= ibu_min and ibu_high <= ibu_max and
            srm_low >= srm_min and srm_high <= srm_max and
            og_low >= og_min and og_high <= og_max and
            fg_low >= fg_min and fg_high <= fg_max
        ):
            continue

        # Lägg till stilen om alla filter matchar
        filtered.append(style)

    return filtered
