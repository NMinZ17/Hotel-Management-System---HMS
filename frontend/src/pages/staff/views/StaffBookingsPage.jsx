import StaffPageHead from '../common/StaffPageHead';

export default function StaffBookingsPage() {
  return (
    <div className="staff-page">
      <StaffPageHead
        title="Thông tin đặt phòng"
        description="Tra cứu thông tin và trạng thái đặt phòng."
      />

      <div className="staff-notice">
        <h3>Chưa kết nối API đặt phòng</h3>
        <p>
          Cần API danh sách đặt phòng và quyền xem dành cho nhân viên
          trước khi hiển thị dữ liệu.
        </p>
      </div>
    </div>
  );
}