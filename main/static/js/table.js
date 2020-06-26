$(document).ready(function () {
    $('#dtBasicExample').DataTable({
      buttons: [
        'copy', 'excel', 'pdf', 'csv'
    ]
  });
    $('.dataTables_length').addClass('bs-select');
    
  });