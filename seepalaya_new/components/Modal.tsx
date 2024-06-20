interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  onFileSelect: (file: File) => void;
}

const Modal: React.FC<ModalProps> = ({ isOpen, onClose, onFileSelect }) => {
  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      onFileSelect(file);
    }
  };

  if (!isOpen) {
    return null;
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center">
      <div className="bg-white p-4 rounded-md w-[90%] max-w-md">
        <h2 className="text-2xl font-bold mb-4">Import CSV</h2>
        <input type="file" accept=".csv" onChange={handleFileChange} />
        <div className="mt-4 flex justify-end">
          <button onClick={onClose} className="mr-2 p-2 bg-gray-200 rounded">
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
};

export default Modal;
