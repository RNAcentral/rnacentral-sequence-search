import React from 'react';

class Footer extends React.Component {
  render() {
    return (
      <footer>
        <div id="global-footer" className="global-footer">
          <nav id="global-nav-expanded" className="global-nav-expanded row">
            <!-- Footer will be automatically inserted by footer.js -->
          </nav>
          <section id="ebi-footer-meta" className="ebi-footer-meta row">
            <!-- Footer meta will be automatically inserted by footer.js -->
          </section>
        </div>
      </footer>
    )
  }
}

export default Footer;
