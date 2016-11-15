$(function () {
    $(".table-container").mCustomScrollbar({
        axis:"x",
        theme: 'dark-3',
        scrollButtons: {
            enable: true
        }
    });

    $(".delete").click(function () {
        return confirm('Вы действительно хотите удалить эту рассылку?');
    });
});