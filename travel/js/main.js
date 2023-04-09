
// появление шапки при скроле на 100 px
(function () {
	const hed = document.querySelector('.hed');
	window.onscroll = () => {
		if (window.pageYOffset > 100) {
			hed.classList.add('hed_active')
		} 
		else {
			hed.classList.remove('hed_active')
		}
	};
}());


// открытие и закрытие меню на мобильных уст-х
(function () {
	const burgerItem = document.querySelector('.burger'); // записали тег в переменную 
	const menu = document.querySelector('.hed__nav')
	const menuCloseItem = document.querySelector('.hed__nav-close')
	burgerItem.addEventListener('click', () => {
		menu.classList.add('hed__nav_active');
	})

	menuCloseItem.addEventListener('click', () => {
		menu.classList.remove('hed__nav_active');
	})
}());


// Scroll to anchors
(function () {

    const smoothScroll = function (targetEl, duration) {
        const headerElHeight =  document.querySelector('.hed').clientHeight;
        let target = document.querySelector(targetEl);
        let targetPosition = target.getBoundingClientRect().top - headerElHeight;
        let startPosition = window.pageYOffset;
        let startTime = null;
    
        const ease = function(t,b,c,d) {
            t /= d / 2;
            if (t < 1) return c / 2 * t * t + b;
            t--;
            return -c / 2 * (t * (t - 2) - 1) + b;
        };
    
        const animation = function(currentTime){
            if (startTime === null) startTime = currentTime;
            const timeElapsed = currentTime - startTime;
            const run = ease(timeElapsed, startPosition, targetPosition, duration);
            window.scrollTo(0,run);
            if (timeElapsed < duration) requestAnimationFrame(animation);
        };
        requestAnimationFrame(animation);

    };

    const scrollTo = function () {
        const links = document.querySelectorAll('.js-scroll');
        links.forEach(each => {
            each.addEventListener('click', function () {
                const currentTarget = this.getAttribute('href');
                smoothScroll(currentTarget, 1000);
            });
        });
    };
    scrollTo();
}());

