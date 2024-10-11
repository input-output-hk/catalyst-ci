---
icon: material/database
hide:
  - navigation
  - toc
---

<!--
  This HTML block configures the page to display a full-width iframe containing the database schema,
  positioned below the header and above the footer removing the second scrollbar.
  
  Key features:
  1. Custom styling to ensure the iframe takes up the full width and available height between header and footer.
  2. JavaScript to dynamically adjust the iframe height and handle internal navigation.
  3. Prevention of the default link behavior inside the iframe to avoid page reloads and flashing.

  The hide metadata removes the navigation and table of contents from the markdown page.
-->

<!-- markdownlint-disable no-inline-html -->
<style>
  iframe {
    position: fixed;
    left: 0;
    width: 100%;
    border: none;
    z-index: 1;
  }
</style>

<iframe src="../database_schema/index.html" id="schemaFrame"></iframe>

<script>
  document.addEventListener('DOMContentLoaded', function() {
    var iframe = document.getElementById('schemaFrame');
    var header = document.querySelector('header');
    var footer = document.querySelector('footer');
    
    function adjustIframePosition() {
      var headerHeight = header.offsetHeight;
      var footerHeight = footer.offsetHeight;
      iframe.style.top = (headerHeight) + 'px';
      iframe.style.height = 'calc(100% - ' + (headerHeight + footerHeight) + 'px)';
    }

    iframe.onload = function() {
      adjustIframePosition();
      
      // Prevent default link behavior inside iframe to avoid page reloads
      iframe.contentWindow.addEventListener('click', function(e) {
        if (e.target.tagName === 'A') {
          e.preventDefault();
          iframe.src = e.target.href;
        }
      }, true);
    };

    // Adjust iframe position and height when window is resized
    window.addEventListener('resize', adjustIframePosition);

    // Initial adjustment
    adjustIframePosition();
  });
</script>