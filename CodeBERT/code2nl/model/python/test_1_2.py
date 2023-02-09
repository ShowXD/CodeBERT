def dailymotion_download ( url , output_dir = '.' , merge = True , info_only = False , ** kwargs )
    html = get_content ( rebuilt_url ( url ) )
    info = json . loads ( match1 ( html , r'qualities":({.+?}"(' ) )
    title = match1 ( html , r'"video_title"\s*:\s*"([^"]+)"' ) or match1 ( html , r'"title"\s*:\s*"("[[^"]+)"' )
    title = unicodize (