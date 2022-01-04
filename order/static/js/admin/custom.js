jQuery.noConflict();
(function($) {
    $(function() {
        var array = ["2021-09-28", "2021-09-29", "2021-09-30"]
        $('#id_date').datepicker({
            beforeShowDay: function(date) {
                var string = $.datepicker.formatDate('yy-mm-dd', date);
                return [array.indexOf(string) == -1]
            }
        });
    });
})(jQuery);
//         console.log(JSON.parse('{{extra_context|safe}}'))
 
//$('datepicker').datepicker({
//     beforeShowDay: function(date) {
//         var string = jQuery.datepicker.formatDate('yy-mm-dd', date);
//         return array.indexOf(string) != -1 ? [false] : $.datepicker.noWeekends(date);
//     }
// });
// var array = [
//     {% for x in disabled_dates %}
//         {{x.dates}}
//     {% endfor  %} 
// ]

// $(document).ready(function() {
//         var array = ["2021-09-28", "2021-09-29", "2021-09-30"]
//         $('#id_date').datepicker({
//             beforeShowDay: function(date) {
//                 var string = jQuery.datepicker.formatDate('yy-mm-dd', date);
//                 return [array.indexOf(string) != -1];
//             }
//         });
//     })


//     // $('input').datepicker({
//     //     beforeShowDay: "2021-09-28"
//     // });
// $('input').datepicker({
//     beforeShowDay: function(date) {
//         var string = jQuery.datepicker.formatDate('yyyy-mm-dd', date);
//         return [array.indexOf(string) == -1]
//     }
// });

// var array = ["04-10-2021", "06-10-2021", "10-10-2021", "15-06-2020"]
// $('input').datepicker({
//     beforeShowDay: function(date) {
//         var string = jQuery.datepicker.formatDate('dd-mm-yyyy', date);
//         return [array.indexOf(string) == -1]
//     }
// });


// $(document).ready(function() {
//     $('.datepicker').datepicker({
//         minDate: 0,
//         beforeShowDay: $.datepicker.noWeekends
//     });
// });