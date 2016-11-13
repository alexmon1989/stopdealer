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

    $('#fell_by_date_from').datetimepicker({
        format: 'DD.MM.YYYY',
        locale: 'ru'
    });

    $('#fell_by_date_to').datetimepicker({
        format: 'DD.MM.YYYY',
        locale: 'ru'
    });

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
});