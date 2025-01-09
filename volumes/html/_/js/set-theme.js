(() => {
    'use strict'

    // const getStoredTheme = () => localStorage.getItem('theme');
    // const setStoredTheme = theme => localStorage.setItem('theme', theme);

    // const getPreferredTheme = () => {
    //     const storedTheme = getStoredTheme();
    //     if (storedTheme) {
    //         return storedTheme;
    //     }

    //     return window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark';
    // }

    const setTheme = theme => {
        console.log('set theme:', theme);
        document.documentElement.setAttribute('data-bs-theme', theme);
    }

    // setTheme(getPreferredTheme());

    window.addEventListener('DOMContentLoaded', () => {
        const dark_theme_switcher = document.getElementById('dark-theme-switch');
        dark_theme_switcher.addEventListener('change', (event) => {
            setTheme(event.currentTarget.checked ? 'dark' : 'light');
        })
    })

    // dark-theme-switch

    // window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
    //     const storedTheme = getStoredTheme();
    //     if (storedTheme !== 'light' && storedTheme !== 'dark') {
    //         setTheme(getPreferredTheme())
    //     }
    // })


    // window.addEventListener('DOMContentLoaded', () => {
    //     // showActiveTheme(getPreferredTheme());

    //     document.querySelectorAll('[data-bs-theme-value]')
    //         .forEach(toggle => { toggle.addEventListener('click', () => {
    //             const theme = toggle.getAttribute('data-bs-theme-value')
    //             // setStoredTheme(theme)
    //             setTheme(theme);
    //             // showActiveTheme(theme, true)
    //         })
    //     })
    // })

})()

// function setTheme (mode = 'auto') {
//   const userMode = localStorage.getItem('bs-theme');
//   const sysMode = window.matchMedia('(prefers-color-scheme: light)').matches;
//   const useSystem = mode === 'system' || (!userMode && mode === 'auto');
//   const modeChosen = useSystem ? 'system' : mode === 'dark' || mode === 'light' ? mode : userMode;

//   if (useSystem) {
//     localStorage.removeItem('bs-theme');
//   } else {
//     localStorage.setItem('bs-theme', modeChosen);
//   }

//   document.documentElement.setAttribute('data-bs-theme', useSystem ? (sysMode ? 'light' : 'dark') : modeChosen);
// //   document.querySelectorAll('.mode-switch .btn').forEach(e => e.classList.remove('text-body'));
// //   document.getElementById(modeChosen).classList.add('text-body');
// }

// setTheme();

// // document.querySelectorAll('.mode-switch .btn').forEach(e => e.addEventListener('click', () => setTheme(e.id)));
// // window.matchMedia('(prefers-color-scheme: light)').addEventListener('change', () => setTheme());
// document.querySelectorAll('[data-bs-theme-value]').forEach(el => {
//     const mode = toggle.getAttribute('data-bs-theme-value');
//     el.addEventListener('click', () => setTheme(mode));
//     // element.classList.remove('active')
//     // element.setAttribute('aria-pressed', 'false')
// })

// alert(document.querySelectorAll('[data-bs-theme-value]'));
