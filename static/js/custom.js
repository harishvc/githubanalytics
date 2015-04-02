$(document).ready(function() {

    var DrawChart = function() {         
    //Create horizontal bar chart using JQuery
    $('.chart').horizBarChart({selector: '.bar',speed: 3000});
    };

    var cleanup = function() {
        $('#searchbox #intro').empty();
        $('#searchbox #intro2').empty();
        $('#askgithub').empty();
        $('#result').empty();
        $('#progress').show();
    }
    
    //Handle Sumbit
    $('#askgithub').submit(function() {
        $('#searchbox #intro').empty();
        $('#result').empty();
        $('#progress').show();
    });
    
    
    //Handle project intro
    if ($('#result').html().trim()) {
        $('#searchbox #intro').hide();
    }
    
    //Bind to hyperlinks 
    $('a.repositoryinfo').bind('click', cleanup);
   
   
    //Find similare repositories on demand
    $('a#findsimilarrepos').bind('click', function() {
        $("#wrapperfindsimilarrepos").empty();
        $("#wrapperfindsimilarrepos").html("finding similar repositories just for you <i class=\"fa fa-spinner fa-spin fa-1x\"></i>");
        var d2 = $.ajax({
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
        $.when( d2 ).done(function(){
            $('a.repositoryinfo').bind('click',cleanup);
        });
        return false;
    });
    
    //Automatically display Horizontal Bar Charts
    if ($('#listlanguages').length > 0) {
           //Step1: Wait for the page to load! 
           $(window).bind("load", function() {
           $("#listlanguages").empty();$("#listlanguages").html("Lising languages <i class=\"fa fa-spinner fa-spin fa-1x\"></i>");
           //Step2: Function call using AJAX
           var d1 = $.ajax({url:'/_listlanguages',dataType:'json', timeout: (60000) ,data: {a: $('input[name="reponame"]').val()},
                  success: function(data) {$("#listlanguages").empty();$("#listlanguages").html(data.languages);},
                  error: function(objAJAXRequest, strError){$("#listlanguages").html("<span class=\"text-danger\">Query taking too long: Please try again latter</span>")} 
                  });
           //Step3: Wait for AJAX to return, attach event handler to the new dynamic element
           $.when( d1 ).done(function(){
            $('#listlanguages').on('click',DrawChart);
            DrawChart(); //trigger a click event
            });
        });
     }
       
});

