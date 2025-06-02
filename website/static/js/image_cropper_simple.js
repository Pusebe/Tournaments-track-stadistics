// image_cropper_simple.js - SIN TOCAR BACKEND
let cropper;

// Cuando se selecciona una imagen
document.getElementById('photo').addEventListener('change', function(e) {
    const file = e.target.files[0];
    
    if (file && file.type.match('image.*')) {
        const reader = new FileReader();
        reader.onload = function(e) {
            document.getElementById('imageToCrop').src = e.target.result;
            $('#cropModal').modal('show');
        };
        reader.readAsDataURL(file);
    }
});

// Cuando se abre el modal
$('#cropModal').on('shown.bs.modal', function() {
    const image = document.getElementById('imageToCrop');
    
    if (cropper) {
        cropper.destroy();
    }
    
    cropper = new Cropper(image, {
        aspectRatio: 1,
        viewMode: 0,
        dragMode: 'move',
        autoCropArea: 0.8,
        preview: '.preview-circle'
    });
});

// Cuando se cierra el modal
$('#cropModal').on('hidden.bs.modal', function() {
    if (cropper) {
        cropper.destroy();
        cropper = null;
    }
});

// AQUÍ ESTÁ LA MAGIA - Convertir canvas a File y reemplazar el input
document.getElementById('cropAndSave').addEventListener('click', function() {
    if (!cropper) return;
    
    const canvas = cropper.getCroppedCanvas({
        width: 300,
        height: 300,
        fillColor: 'transparent' // Fondo transparente
    });
    
    canvas.toBlob(function(blob) {
        // Crear un nuevo File object con el blob
        const croppedFile = new File([blob], 'cropped_image.png', {
            type: 'image/png', // Cambiar a PNG para soportar transparencia
            lastModified: Date.now()
        });
        
        // TRUCO: Crear un nuevo FileList con la imagen recortada
        const dataTransfer = new DataTransfer();
        dataTransfer.items.add(croppedFile);
        
        // Reemplazar el contenido del input file original
        document.getElementById('photo').files = dataTransfer.files;
        
        // Actualizar preview
        const url = URL.createObjectURL(blob);
        document.getElementById('profileImage').src = url;
        
        // Cerrar modal
        $('#cropModal').modal('hide');
        
        console.log('Imagen recortada lista para enviar!');
        
    }, 'image/png', 0.85);
});