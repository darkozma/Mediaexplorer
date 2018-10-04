# -*- coding: utf-8 -*-
from core.libs import *
import zipfile


def extract(fname, dest, overwrite=False, silent=False):
    logger.trace()
    import shutil
    created_dest = canceled = False
    zf = zipfile.ZipFile(fname)
    
    if not os.path.isdir(dest): 
        os.makedirs(dest)
        created_dest = True


    if silent:
        # Descomprimimos en modo silencioso (mas rapido)
        zf.extractall(dest)
    else:
        # Descomprimimos mostrando el cuadro de progreso y permitiendo cancelar
        dialog = platformtools.dialog_progress('Extrayendo', '')
        uncompress_size = sum((file.file_size for file in zf.infolist()))
        extracted_size = num_files= count= 0

        # Crear destino temporal
        dest_tmp = dest + "_TMP"
        if not os.path.isdir(dest_tmp):
            os.makedirs(dest_tmp)

        for file in zf.infolist():
            extracted_size += file.file_size
            porcent = extracted_size * 100 / uncompress_size
            num_files += 1
            dialog.update(porcent,
                          "Descomprimiendo:",
                          ".../%s" % file.filename[-60:].split('/',1)[1] if len(file.filename) > 60 else file.filename,
                          "Fichero %s de %s (%s%%)"  % (num_files, len(zf.infolist()),porcent))

            if dialog.iscanceled():
                canceled = True
                break
            zf.extract(file, dest_tmp)

        if not canceled:
            list_remove = []
            # Mover desde la carpeta temporal a la carpeta destino
            for root, dirs, files in os.walk(dest_tmp):
                if overwrite and root == dest_tmp:
                    for d in dirs:
                        d = os.path.join(dest, d)
                        if os.path.isdir(d):
                            os.rename(d, d + "_bak")
                            list_remove.append( d + "_bak")

                    for f in files:
                        f = os.path.join(dest, f)
                        if os.path.isfile(f):
                            os.rename(f, f + '.bak')
                            list_remove.append(f + '.bak')

                for filename in files:
                    filepath_src = os.path.join(root, filename)
                    filepath_dest = filepath_src.replace(dest_tmp, dest, 1)
                    dirname_dest = os.path.dirname(filepath_dest)
                    if not os.path.isdir(dirname_dest):
                        os.makedirs(dirname_dest)
                    count += 1
                    porcent = count * 100 / num_files
                    dialog.update(porcent,
                                  "Moviendo:",
                                  ".../%s" % filepath_dest[-60:].split(os.sep, 1)[1] if len(filepath_dest) > 60 else filepath_dest,
                                  "Fichero %s de %s (%s%%)" % (count, num_files, porcent))
                    shutil.move(filepath_src, filepath_dest)

                for i in list_remove:
                    if os.path.isdir(i):
                        shutil.rmtree(i, ignore_errors=True)
                    elif os.path.isfile(i):
                        os.remove(i)

        elif created_dest:
            os.rmdir(dest)

        shutil.rmtree(dest_tmp, ignore_errors=True)
        dialog.close()

    zf.close()

    return not canceled