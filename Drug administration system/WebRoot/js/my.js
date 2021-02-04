$(function(){
	var usertype = $.cookie("usertype")
	if (usertype==1) {
		$("#list1").hide();
		$("#list2").hide();
	} else if(usertype==2){
		$("#list1").hide();
		$("#list3").hide();
	}
	  
})