def filter_styles(styles, category=None, abv_min=0, abv_max=100, ibu_min=0, ibu_max=1000, srm_min=0, srm_max=100, og_min=0, og_max=2, fg_min=0, fg_max=2):
    """
    Filter beer styles based on various criteria.
    
    Returns a filtered list of styles that match all specified criteria.
    """
    filtered = []
    
    for style in styles:
        # Skip if category doesn't match (if specified)
        if category and style.get('category', '').lower() != category.lower():
            continue
            
        # Check numerical ranges - convert strings to floats where needed
        # ABV check
        style_abv_min = float(style.get('abvmin', 0))
        style_abv_max = float(style.get('abvmax', 100))
        if style_abv_min > abv_max or style_abv_max < abv_min:
            continue
            
        # IBU check
        style_ibu_min = float(style.get('ibumin', 0))
        style_ibu_max = float(style.get('ibumax', 1000))
        if style_ibu_min > ibu_max or style_ibu_max < ibu_min:
            continue
            
        # SRM check
        style_srm_min = float(style.get('srmmin', 0))
        style_srm_max = float(style.get('srmmax', 100))
        if style_srm_min > srm_max or style_srm_max < srm_min:
            continue
            
        # OG check
        style_og_min = float(style.get('ogmin', 0))
        style_og_max = float(style.get('ogmax', 2))
        if style_og_min > og_max or style_og_max < og_min:
            continue
            
        # FG check
        style_fg_min = float(style.get('fgmin', 0))
        style_fg_max = float(style.get('fgmax', 2))
        if style_fg_min > fg_max or style_fg_max < fg_min:
            continue
            
        # If we got here, all filters passed
        filtered.append(style)
        
    return filtered
