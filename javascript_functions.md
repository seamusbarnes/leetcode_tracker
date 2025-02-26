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
