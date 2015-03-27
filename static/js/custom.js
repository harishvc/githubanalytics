$(document).ready(function() {
    $('#askgithub').submit(function() {
        $('#searchbox #intro').empty();
        $('#result').empty();
        $('#progress').show();
    });
    if ($('#result').html().trim()) {
        $('#searchbox #intro').hide();
    }
    $('a#findsimilarrepos').bind('click', function() {
        $("#wrapperfindsimilarrepos").empty();
        $("#wrapperfindsimilarrepos").html("finding similar repositories just for you <i class=\"fa fa-spinner fa-spin fa-1x\"></i>");
        $.ajax({
            url : '/_findsimilarrepositories',
            dataType : 'json',
            timeout : (60000),
            data : {
                a : $('input[name="reponame"]').val()
            },
            success : function(data) {
                $("#similarrepos").html(data.similarrepos);
                $("#wrapperfindsimilarrepos").empty();
            },
            error : function(objAJAXRequest, strError) {
                $("#similarrepos").html("<span class=\"text-danger\">Query taking too long: Please try again latter</span>");
                $("#wrapperfindsimilarrepos").empty();
            }
        });
        return false;
    });
    //Wait for DOM to load and then call function
    if ($('#listlanguages').length > 0) { 
               $(window).bind("load", function() {
                    $("#listlanguages").empty();$("#listlanguages").html("Lising languages <i class=\"fa fa-spinner fa-spin fa-1x\"></i>");
                    $.ajax({url:'/_listlanguages',dataType:'json', timeout: (60000) ,data: {a: $('input[name="reponame"]').val()},
                        success: function(data) {$("#listlanguages").empty();$("#listlanguages").html(data.languages);},
                        error: function(objAJAXRequest, strError){$("#listlanguages").html("<span class=\"text-danger\">Query taking too long: Please try again latter</span>")} 
                    });
               });
     }
});

