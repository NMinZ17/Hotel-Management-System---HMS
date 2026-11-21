import StaffPageHead from '../common/StaffPageHead';

export default function StaffGuestsPage() {
  return (
    <div className="staff-page">
      <StaffPageHead
        title="Thông tin khách hàng"
        description="Tra cứu thông tin khách hàng và khách lưu trú."
      />

      <div className="staff-notice">
        <h3>Chưa kết nối API khách hàng</h3>
        <p>
          Backend cần cung cấp API danh sách khách hàng và quyền truy cập
          dành cho nhân viên. Hiện tại chưa có dữ liệu để hiển thị.
        </p>
      </div>
    </div>
  );
}