// Project: VSTS Discovery extension
// JavaScript functions for controlling main page behaviours
// Author: Yichen Lu
// Create Date: 31-Jan-2017
// Update Date: 01-Feb-2017

jQuery(document).ready(function() {
    $($('#navbar ul').children().get(0)).addClass('active');
    // activate status component when page loaded by default
    removeActiveClassInMenuItems();
    $('#status').addClass('active');
    // $('#navbar').find('li').first().addClass('active')
    load100PtStatus();

});

$('#status').click(function(event) {
    event.preventDefault();
    removeActiveClassInMenuItems();
    $(this).addClass('active');
    load100PtStatus();
});

$('#assign').click(function(event) {
    event.preventDefault();
    removeActiveClassInMenuItems();
    $(this).addClass('active');
    $('#100-points-components').load("components/100-points-assign.html");
});

function removeActiveClassInMenuItems() {
    $("#100-points-menu li").removeClass('active');
}

VSS.getAppToken().then(function(token){
    console.log(token);
});