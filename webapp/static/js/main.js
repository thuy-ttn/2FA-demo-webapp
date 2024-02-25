
$("document").ready(function() {
    $(".login-button").click(function(e) {
		$.ajax({
			"url": "/login",
			"type": "POST",
			data: {
                username: $("#username").val(),
                password: $("#password").val()
            },
			"success": function(data) {
				if (data["enable_2FA"] == 1) {
					// show the verification code input box
					$(".box-1").css({
						"display": "none"
					});
					$(".box-2").css({
						"display": "block"
					});
					$(".events li:nth-child(2)").addClass('progress-2');
					$(".progress-step-2").addClass('progress-bar-fill');
				} else{
                    //redirect to homepage
					$(window).attr('location','/home')
                }
			},
			"error": function(er) {
				alert(JSON.parse(er['responseText']).error)
			}
		});
	});

	$(".register-2fa-button").click(function(e) {
		$.ajax({
			"url": "/register-2fa",
			"type": "POST",
			data: {
                username: $("#username").val()
            },
			"success": function(data) {
				if (data["img"] != null) {
					// show the QR code div
					$(".qr-code").css({
						"display": "block"
					});
					
					//Fetching img data
					base64Data = data["img"]
					var imageElement = $('<img>').attr('src', "data:image/png;base64," + base64Data);
					var container = $("#img-container");
					container.empty(); // Clear previous content
					container.append(imageElement);
				} else{
                    //redirect to homepage
					$(window).attr('location','/home')
                }
			},
			"error": function(er) {
				console.log(er)
			}
		});
	});

	$("#finish-2fa").click(function(e){
		$(window).attr('location','/')
	});

	$(".verification-code-check-button").click(function(e) {
		$.ajax({
			"url": "/verify-2fa",
			"type": "POST",
			data: {
                otp: $("#otp").val()
            },
			"success": function(data) {
				if (data["status"] == "success") {
					// $('input[type="text"]').removeClass('error-text-box');
					// $(".progress-step-2").addClass('progress-bar-fill');
					// $('.box-2').addClass('success');
					$(window).attr('location','/home')
				} else {
					$('input[type="text"]').addClass('error-text-box');
					$('.error-text').css('display', 'block');
				}
			},
			"error": function(er) {
				console.log(er);
			}
		});
	});
})