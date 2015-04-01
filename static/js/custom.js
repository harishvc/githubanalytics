$(document).ready(function() {
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
    $('a.repositoryinfo').bind('click', function() {
        $('#searchbox #intro').empty();
        $('#searchbox #intro2').empty();
         $('#askgithub').empty();
        $('#result').empty();
        $('#progress').show();
    });
  
  
    $("a").on("click", "repositoryinfo", function(event){
        alert($(this).text());
    });
  
    //Find similare repositories on demand
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
         
    //Create horizontal bar chart using JQuery
    $('.chart').horizBarChart({selector: '.bar',speed: 3000});
      
});

