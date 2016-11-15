/**
 * Получение моделей авто согласно выбранному производителю.
 */
var getModels = function () {
    $("#model").attr("disabled", true);
    $("#model").empty();
    $.getJSON( "/cabinet/cheapened_autos/get-models/" + $("#manufacturer").val() + '/', function( data ) {
        $("#model").append( $('<option value=""></option>'));
        $.each(data, function (key, val) {
            $("#model").append( $('<option value="' + val + '">' + val + '</option>'));
        });
        $("#model").attr("disabled", false);
    });
};

$(function () {
    if (!$("#manufacturer").val()) {
        $("#model").attr("disabled", true);
    }

    /**
     * Обработчик события изменния производителя
     */
    $("#manufacturer").change(function () {
        if ($("#manufacturer").val()) {
            getModels();
        } else {
            $("#model").empty();
            $("#model").attr("disabled", true);
        }
    });

    // Maskedit для поля price_from
    $('#price_from').mask('000 000 000 000 000 000', {reverse: true});
    // Maskedit для поля price_to
    $('#price_to').mask('000 000 000 000 000 000', {reverse: true});
    $('#price_from, #price_to').blur(function () {
        var intValue = parseInt($(this).val().replace(' ', ''));
        if (intValue < 1000) {
            $(this).mask('');
            $(this).val(intValue * 1000);
            $(this).mask('000 000 000 000 000 000', {reverse: true});
        }
    });
});