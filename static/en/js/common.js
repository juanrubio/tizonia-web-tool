/* *** Language Selector *** */

$('.headerWrapper select').change(function(){
    var url = 'http://tizonia.org/';
    var lang = $(this).val();
    if (lang != 'en') {
        url += lang + '/';
    }
    window.location.href = url;
});