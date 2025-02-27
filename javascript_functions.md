Run the following javascript command in the console of the inspect window for the webpage to download the raw html to downloads. If you write this code in the the address of a safari bookmark, the javascript will run as if it's in the console, downloading the page.

```javascript
javascript: (function () {
  let content = document.documentElement.outerHTML;
  let blob = new Blob([content], { type: "text/html" });
  let link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = document.title + ".html";
  link.click();
})();
```

On the leetcode progress page there is a button to espand the view of the problem, to see the date, result, language, runtime and memory of each submission. In the .html it is the following line:

```html
<div title="Toggle Row Expanded" style="cursor: pointer;"></div>
```

To click this button using javascript, you can run the following command:

```javascript
const btn = document.querySelector('div[title="Toggle Row Expanded"]');
if (btn) {
  btn.click();
}
```

To open and close the expanded view, run the following:

```javascript
const btn = document.querySelector('div[title="Toggle Row Expanded"]');
if (btn) {
  // First click
  btn.click();
  // Wait 1 second, then click again
  setTimeout(() => {
    btn.click();
  }, 1000);
}
```

If `btn` has already been defined in the workspace, this command will give a SyntaxError: `SyntaxError: Can't create duplicate variable: 'btn'`, in which cas you need to restart the workspace, rename the variable, or run the code with the variable nested locally within a function:

```javascript
javascript: (function () {
  var btn = document.querySelector('div[title="Toggle Row Expanded"]');
  if (btn) {
    btn.click();
    setTimeout(function () {
      btn.click();
    }, 1000);
  }
})();
```

If you want to click all the buttons of this type. with `div[title="Toggle Row Expanded"]`, you can run the following command, which can also be turned into a bookmark by putting it in the bookmark url:

With 1 s delay

```javascript
javascript: (function () {
  var togglerList = document.querySelectorAll(
    'div[title="Toggle Row Expanded"]'
  );
  togglerList.forEach(function (toggler, i) {
    setTimeout(function () {
      toggler.click();
    }, 1000 * i);
  });
})();
```

With no delay

```javascript
javascript: (function () {
  var togglerList = document.querySelectorAll(
    'div[title="Toggle Row Expanded"]'
  );
  togglerList.forEach(function (toggler) {
    toggler.click();
  });
})();
```

When you expand the row, if you have more than 10 submissions for a problem, they are shown in in separate lists, which you can scroll through by pressing a button with the tag `button[aria-label="next"]`:

```javascript
javascript: (function () {
  function clickNextRepeatedly() {
    // Find the 'next' button on the page
    var nextBtn = document.querySelector('button[aria-label="next"]');

    // If it exists and is not disabled, click it and repeat
    if (nextBtn && !nextBtn.disabled) {
      nextBtn.click();
      // Wait a moment for the new page of results to load, then try again
      setTimeout(clickNextRepeatedly, 1000);
    }
    // Otherwise, we stop
  }

  clickNextRepeatedly();
})();
```

You can also expand all the rows and scan through the lists using the following code, you have to make sure you don't also click on the "next" button in the bottom navigation bar, otherwise the script will open everything, scan through everything, and then navigate through the next pages:

```javascript
javascript: (function () {
  function sleep(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }

  async function openAllAndPaginate() {
    // 1) Click all toggler buttons
    const togglers = document.querySelectorAll(
      'div[title="Toggle Row Expanded"]'
    );
    togglers.forEach((toggler) => toggler.click());

    // Give the newly revealed tables a moment to render
    await sleep(500);

    // 2) Find all "next" buttons in the submissions tables, ignoring the bottom nav
    let nextButtons = Array.from(
      document.querySelectorAll('button[aria-label="next"]')
    );
    nextButtons = nextButtons.filter((btn) => {
      const nav = btn.closest("nav");
      // Skip if it's the bottom nav (which has class "mb-0")
      return nav && !nav.classList.contains("mb-0");
    });

    // 3) For each "next" button, keep clicking until it's disabled
    for (const btn of nextButtons) {
      while (!btn.disabled) {
        btn.click();
        // Slight delay between clicks
        await sleep(50);
      }
    }

    // Done! All dropdowns have been opened, and each table's "next" pages have been revealed.
  }

  openAllAndPaginate();
})();
```
