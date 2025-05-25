function errorInFetchingData(){
    console.log("Error in retrieving data");

    Swal.fire({
        title: 'Error in Retrieving Data',
        html: 'Please check your internet connection<br>or selected date',
        icon: 'error',
        confirmButtonText: 'OK'
    });
}

function errorInSummary(){
    console.log("Error in creating summary");
                    
    Swal.fire({
        title: 'Error!',
        text: 'Failed to retrieve summary',
        icon: 'error',
        confirmButtonText: 'OK'
    });
}

//---------------------AJAX-------------------------------
// GET RAW DATA BUTTON
$(function () {
    $('.form1').submit(function (e) {
        e.preventDefault();

        Swal.fire({
            title: 'Retrieving Data',
            html: `The data is being retreived from AWS.<br><br>
        The file is over 200MB in size, and after downloading will require some time for processing.<br>`,
            timer: 600000,
            timerProgressBar: false,
            didOpen: () => { Swal.showLoading() }
        }).then((result) => {
            /* Read more about handling dismissals below */
            if (result.dismiss === Swal.DismissReason.timer) {
                errorInFetchingData();
            }
        });

        var form = $(this);
        var actionUrl = form.attr('action');
        console.log("Date : ", $('#select-date').val());

        $.ajax({
            type: 'POST',
            url: "/run_application",
            data: { selected_date: $('#select-date').val() },
            success: function (data) {
                console.log(data);
                if (data != 'ERROR') {
                    $('.downloadSummary').removeAttr('disabled');
                    console.log("Data Retrieved from AWS");

                    Swal.fire({
                        title: 'Data Processed',
                        text: 'The summary can now be downloaded',
                        icon: 'success',
                        confirmButtonText: 'OK'
                    });
                } else {
                    errorInFetchingData();
                }
            },
            error: function (data) {
                errorInFetchingData();
            }
        });
    });
});


// DOWNLOAD Button
$(function () {
    $('.form2').submit(function (e) {
        e.preventDefault();
        var form = $(this);
        var actionUrl = form.attr('action');
        console.log("Creating Summary");

        $.ajax({
            type: 'GET',
            url: "/download_data",
            success: function (data) {
                console.log(data);
                if (data != 'ERROR') {
                    console.log("Summary File Created");
                    Swal.fire({
                        title: 'Succcess!',
                        text: 'Summary has been downloaded',
                        icon: 'success',
                        confirmButtonText: 'OK'
                    });
                } else {
                    errorInSummary();
                }
            },
            error: function (data) {
                errorInSummary();
            }
        });
    });
});