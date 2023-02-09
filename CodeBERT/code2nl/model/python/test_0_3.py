2	def sina_download ( url , output_dir = '.' , merge = True , info_only = False , ** kwargs ) :
    if 'news.sina.com.cn/zxt' in url :
        sina_zxt ( url , output_dir = output_dir , merge = merge , info_only = info_only , ** kwargs )
        return vid = match1 ( url , r'vid=(\d+)' )
        if vid is None :
            video_page = get_content ( url ) vid = hd_vid = match1 (