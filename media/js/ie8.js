$(document).ready(function () {
    $('label[for="publicpc1"]').click(function(){
        var ch = $('input[id="publicpc"]');

        if(ch.attr("checked")){
            ch.removeAttr("checked")
        }else{
            ch.attr("checked", "checked");
        }

        $(this).toggleClass('checked');
    });

    $('label[for="publicpc"]').click(function(){
        var ch = $('input[id="publicpc"]');

        if(ch.attr("checked")){
            ch.removeAttr("checked")
        }else{
            ch.attr("checked", "checked");
        }

        $(this).toggleClass('checked');
    });



});
