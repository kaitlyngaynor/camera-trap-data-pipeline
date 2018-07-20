###################################
# Ruaha
####################################

# Create Zooniverse password file in home directory
# Example: zooniverse.ini
# chmod 600 zooniverse.ini
# username: XYZ
# password: 1234

# Generate Manifest
cd /home/packerc/shared/machine_learning/will5448/code/snapshot_safari_misc
python3 -m zooniverse_uploads.generate_manifest \
-cleaned_captures_csv /home/packerc/shared/season_captures/RUA/cleaned/RUA_S1_cleaned.csv \
-compressed_image_dir /home/packerc/shared/zooniverse/ToUpload/RUA/RUA_S1_Compressed/ \
-output_manifest_dir /home/packerc/shared/zooniverse/Manifests/RUA/ \
-manifest_prefix RUA_S1 \
-attribution 'University of Minnesota Lion Center + SnapshotSafari + Ruaha Carnivore Project + Tanzania + Ruaha National Park' \
-license 'SnapshotSafari + Ruaha Carnivore Project'

# OPTIONAL (hack) - Remove specific capture events from the manifest
cd /home/packerc/shared/machine_learning/will5448/code/snapshot_safari_misc
python3 -m zooniverse_uploads.remove_records_from_manifest \
-manifest /home/packerc/shared/zooniverse/Manifests/RUA/RUA_S1_manifest.json \
-old_manifest_to_remove /home/packerc/shared/zooniverse/Manifests/RUA/RUA_S1_A1_manifest_v1 \
-season RUA_S1

# Create Prediction Info File for Machine Lerning Model
cd /home/packerc/shared/machine_learning/will5448/code/snapshot_safari_misc
python3 -m zooniverse_uploads.create_predict_file_from_manifest \
-manifest /home/packerc/shared/zooniverse/Manifests/RUA/RUA_S1_manifest.json \
-prediction_file /home/packerc/shared/machine_learning/data/info_files/RUA/RUA_S1/RUA_S1_manifest.csv

# Generate new Predictions
cd /home/packerc/shared/machine_learning/will5448/code/snapshot_safari_misc/machine_learning/jobs
# ADAPT predict_species.pbs
# ADAPT predict_empty.pbs

ssh mesabi
qsub predict_species.pbs
qsub predict_empty.pbs

# Aggregte Predictions
cd /home/packerc/shared/machine_learning/will5448/code/snapshot_safari_misc
python3 -m zooniverse_uploads.import_and_aggregate_predictions \
-manifest /home/packerc/shared/zooniverse/Manifests/RUA/RUA_S1_manifest.json \
-empty_predictions /home/packerc/shared/machine_learning/data/predictions/empty_or_not/RUA/RUA_S1/predictions_run_SER_old_manifest_20180719.json \
-species_predictions /home/packerc/shared/machine_learning/data/predictions/species/RUA/RUA_S1/predictions_run_SER_old_manifest_20180719.json \
-output_file /home/packerc/shared/zooniverse/Manifests/RUA/RUA_S1_preds_aggregated.json


# Merge Predictions into Manifest
cd /home/packerc/shared/machine_learning/will5448/code/snapshot_safari_misc
python3 -m zooniverse_uploads.merge_predictions_with_manifest \
-manifest /home/packerc/shared/zooniverse/Manifests/RUA/RUA_S1_manifest.json \
-predictions /home/packerc/shared/zooniverse/Manifests/RUA/RUA_S1_preds_aggregated.json \
-output_file /home/packerc/shared/zooniverse/Manifests/RUA/RUA_S1_manifest1.json


# Upload Manifest
cd /home/packerc/shared/machine_learning/will5448/code/snapshot_safari_misc
python3 -m zooniverse_uploads.upload_manifest \
-manifest /home/packerc/shared/zooniverse/Manifests/RUA/RUA_S1_manifest1.json \
-output_file /home/packerc/shared/zooniverse/Manifests/RUA/RUA_S1_manifest2.json \
-project_id 5155 \
-subject_set_name RUA_S1_machine_learning_v1 \
-password_file ~/keys/passwords.ini


###################################
# Serengeti
####################################

# Generate Manifest
cd /home/packerc/shared/machine_learning/will5448/code/snapshot_safari_misc
python3 -m zooniverse_uploads.generate_manifest \
-cleaned_captures_csv /home/packerc/shared/season_captures/SER/cleaned/SER_S11_cleaned_V3.csv \
-compressed_image_dir /home/packerc/shared/zooniverse/ToUpload/SER/SER_S11_Compressed/ \
-output_manifest_dir /home/packerc/shared/zooniverse/Manifests/SER/ \
-manifest_prefix SER_S11 \
-attribution 'University of Minnesota Lion Center + SnapshotSafari + Snapshot Serengeti + Serengeti National Park + Tanzania' \
-license 'SnapshotSafari + Snapshot Serengeti'


# OPTIONAL (hack) - Remove specific capture events from the manifest
cd /home/packerc/shared/machine_learning/will5448/code/snapshot_safari_misc
python3 -m zooniverse_uploads.remove_records_from_manifest \
-manifest /home/packerc/shared/zooniverse/Manifests/SER/SER_S11_manifest.json \
-old_manifest_to_remove /home/packerc/shared/zooniverse/Manifests/SER/SER_S11_1_manifest_v1 \
-season SER_S11

cd /home/packerc/shared/machine_learning/will5448/code/snapshot_safari_misc
python3 -m zooniverse_uploads.remove_records_from_manifest \
-manifest /home/packerc/shared/zooniverse/Manifests/SER/SER_S11_manifest.json \
-old_manifest_to_remove /home/packerc/shared/zooniverse/Manifests/SER/SER_S11_2_manifest_v1 \
-season SER_S11

cd /home/packerc/shared/machine_learning/will5448/code/snapshot_safari_misc
python3 -m zooniverse_uploads.remove_records_from_manifest \
-manifest /home/packerc/shared/zooniverse/Manifests/SER/SER_S11_manifest.json \
-old_manifest_to_remove /home/packerc/shared/zooniverse/Manifests/SER/SER_S11_3_manifest_v1.csv \
-season SER_S11


# Create Prediction Info File for Machine Lerning Model
cd /home/packerc/shared/machine_learning/will5448/code/snapshot_safari_misc
python3 -m zooniverse_uploads.create_predict_file_from_manifest \
-manifest /home/packerc/shared/zooniverse/Manifests/SER/SER_S11_manifest.json \
-prediction_file /home/packerc/shared/machine_learning/data/info_files/SER/SER_S11/SER_S11_manifest.csv

# Generate new Predictions
cd /home/packerc/shared/machine_learning/will5448/code/snapshot_safari_misc/machine_learning/jobs
# ADAPT predict_species.pbs
# ADAPT predict_empty.pbs

ssh mesabi
qsub predict_species.pbs
qsub predict_empty.pbs

# Aggregte Predictions
cd /home/packerc/shared/machine_learning/will5448/code/snapshot_safari_misc
python3 -m zooniverse_uploads.import_and_aggregate_predictions \
-manifest /home/packerc/shared/zooniverse/Manifests/SER/SER_S11_manifest.json \
-empty_predictions /home/packerc/shared/machine_learning/data/predictions/empty_or_not/SER/SER_S11/predictions_run_SER_old_manifest_20180719.json \
-species_predictions /home/packerc/shared/machine_learning/data/predictions/species/SER/SER_S11/predictions_run_SER_old_manifest_20180719.json \
-output_file /home/packerc/shared/zooniverse/Manifests/SER/SER_S11_preds_aggregated.json


# Merge Predictions into Manifest
cd /home/packerc/shared/machine_learning/will5448/code/snapshot_safari_misc
python3 -m zooniverse_uploads.merge_predictions_with_manifest \
-manifest /home/packerc/shared/zooniverse/Manifests/SER/SER_S11_manifest.json \
-predictions /home/packerc/shared/zooniverse/Manifests/SER/SER_S11_preds_aggregated.json \
-output_file /home/packerc/shared/zooniverse/Manifests/SER/SER_S11_manifest1.json


# Upload Manifest
cd /home/packerc/shared/machine_learning/will5448/code/snapshot_safari_misc
python3 -m zooniverse_uploads.upload_manifest \
-manifest /home/packerc/shared/zooniverse/Manifests/SER/SER_S11_manifest1.json \
-output_file /home/packerc/shared/zooniverse/Manifests/SER/SER_S11_manifest2.json \
-project_id 5155 \
-subject_set_name SER_S11_machine_learning_v1 \
-password_file ~/keys/passwords.ini