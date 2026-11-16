
import './Header.css';

const Header = ({
  title = 'HOTEL MANAGEMENT',
  links = [],
  userName = '',
  onLogout,
  showLogout = true,
}) => {
  return (
    <header className="common-header">
      <div className="common-header__brand">
        {title}
      </div>

      <nav className="common-header__nav">
        {links.map((link) => (
          <a
            key={link.href}
            href={link.href}
            className="common-header__link"
          >
            {link.label}
          </a>
        ))}
      </nav>

      <div className="common-header__actions">
        {userName && (
          <span className="common-header__username">
            {userName}
          </span>
        )}

        {showLogout && onLogout && (
          <button
            type="button"
            className="common-header__logout"
            onClick={onLogout}
          >
            Đăng xuất
          </button>
        )}
      </div>
    </header>
  );
};

export default Header;
