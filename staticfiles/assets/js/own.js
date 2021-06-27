$("#inputGameType").change(function() {
    console.log("OK 2")
    if ($(this).val() == "T3 Scrims") {
        $('#add-day-forGameTypeDiv').show()
    } else {
        $('#add-day-forGameTypeDiv').hide();
        }
});
$("#inputGameType").trigger("change");