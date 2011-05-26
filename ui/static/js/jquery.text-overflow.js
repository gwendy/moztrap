/**
 * jQuery Text-overflow
 *
 * http://devongovett.wordpress.com/2009/04/06/text-overflow-ellipsis-for-firefox-via-jquery/
 *
 */

(function($) {
	$.fn.ellipsis = function(enableUpdating){
		var s = document.documentElement.style;
		if (!('textOverflow' in s || 'OTextOverflow' in s)) {
			return this.each(function(){
				var el = $(this);
				if(el.css("overflow") == "hidden"){
					var originalText = el.html();
					var w = el.width();

					var t = $(this.cloneNode(true)).hide().css({
                        'position': 'absolute',
                        'width': 'auto',
                        'overflow': 'visible',
                        'max-width': 'inherit'
                    });
					el.after(t);

					var text = originalText;
					while(text.length > 0 && t.width() > el.width()){
						text = text.substr(0, text.length - 1);
						t.html(text + "...");
					}
					el.html(t.html());

					t.remove();

					if(enableUpdating == true){
						var oldW = el.width();
						$(window).resize(function(){
							if(el.width() != oldW){
								oldW = el.width();
								el.html(originalText);
								el.ellipsis();
							}
						});
					}
				}
			});
		} else return this;
	};
})(jQuery);