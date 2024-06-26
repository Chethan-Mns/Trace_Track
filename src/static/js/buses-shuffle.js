function busesShuffle() {
    "use strict";
    var myShuffle;
    if ($('.shuffle-wrapper').length !== 0) {
        var Shuffle = window.Shuffle;
        myShuffle = new Shuffle(document.querySelector('.shuffle-wrapper'), {
            itemSelector: '.shuffle-item',
            sizer: '.shuffle-sizer',
            buffer: 1
        });
        $('input[name="shuffle-filter"]').on('change', function (evt) {
            var input = evt.currentTarget;
            if (input.checked) {
                myShuffle.filter(input.value);
            }
        });
        $('.shuffle-btn-group label').on('click', function () {
            $('.shuffle-btn-group label').removeClass('active');
            $(this).addClass('active');
        });
    }
};
busesShuffle();