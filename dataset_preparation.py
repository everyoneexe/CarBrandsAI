#!/usr/bin/env python3
"""
Car Brand Logo Dataset Preparation Utility
Bu script, car brand logo detection için dataset hazırlamaya yardımcı olur.
"""

import os
import shutil
from pathlib import Path
import random
import yaml
from typing import List, Tuple
import cv2
import numpy as np

class CarBrandDatasetPreparator:
    def __init__(self, source_dataset_path: str, target_dataset_path: str):
        """
        Args:
            source_dataset_path: Ham dataset'in bulunduğu yol
            target_dataset_path: YOLO formatında organize edilecek dataset yolu
        """
        self.source_path = Path(source_dataset_path)
        self.target_path = Path(target_dataset_path)
        
        # YOLO dataset yapısını oluştur
        self.train_images = self.target_path / "train" / "images"
        self.train_labels = self.target_path / "train" / "labels"
        self.valid_images = self.target_path / "valid" / "images"
        self.valid_labels = self.target_path / "valid" / "labels"
        self.test_images = self.target_path / "test" / "images"
        self.test_labels = self.target_path / "test" / "labels"
        
        # Klasörleri oluştur
        for path in [self.train_images, self.train_labels, 
                    self.valid_images, self.valid_labels,
                    self.test_images, self.test_labels]:
            path.mkdir(parents=True, exist_ok=True)
    
    def get_car_brands(self) -> List[str]:
        """Dataset'teki marka isimlerini otomatik olarak tespit et"""
        brands = set()
        
        # Source dataset'te klasör yapısına göre markaları bul
        for item in self.source_path.iterdir():
            if item.is_dir():
                brands.add(item.name.lower())
        
        return sorted(list(brands))
    
    def create_data_yaml(self, brands: List[str]):
        """YOLO eğitimi için data.yaml dosyasını oluştur"""
        yaml_content = {
            'path': str(self.target_path.absolute()),
            'train': 'train/images',
            'val': 'valid/images',
            'test': 'test/images',
            'nc': len(brands),
            'names': brands
        }
        
        with open(self.target_path / "data.yaml", 'w') as f:
            yaml.dump(yaml_content, f, default_flow_style=False)
        
        print(f"data.yaml created with {len(brands)} classes: {', '.join(brands)}")
    
    def split_dataset(self, train_ratio: float = 0.7, valid_ratio: float = 0.2, test_ratio: float = 0.1):
        """Dataset'i train/valid/test olarak böl"""
        assert abs(train_ratio + valid_ratio + test_ratio - 1.0) < 1e-6, "Ratios must sum to 1.0"
        
        brands = self.get_car_brands()
        brand_to_id = {brand: idx for idx, brand in enumerate(brands)}
        
        total_images = 0
        
        for brand in brands:
            brand_path = self.source_path / brand
            if not brand_path.exists():
                continue
                
            # Marka klasöründeki tüm görselleri bul
            image_files = []
            for ext in ['*.jpg', '*.jpeg', '*.png', '*.bmp']:
                image_files.extend(list(brand_path.glob(ext)))
                image_files.extend(list(brand_path.glob(ext.upper())))
            
            if not image_files:
                print(f"Warning: No images found for brand {brand}")
                continue
            
            # Rastgele karıştır
            random.shuffle(image_files)
            
            # Train/valid/test split
            n_total = len(image_files)
            n_train = int(n_total * train_ratio)
            n_valid = int(n_total * valid_ratio)
            
            train_files = image_files[:n_train]
            valid_files = image_files[n_train:n_train + n_valid]
            test_files = image_files[n_train + n_valid:]
            
            # Dosyaları kopyala ve label oluştur
            brand_id = brand_to_id[brand]
            
            self._copy_and_label_images(train_files, self.train_images, self.train_labels, brand_id, brand)
            self._copy_and_label_images(valid_files, self.valid_images, self.valid_labels, brand_id, brand)
            self._copy_and_label_images(test_files, self.test_images, self.test_labels, brand_id, brand)
            
            total_images += len(image_files)
            print(f"{brand}: {len(train_files)} train, {len(valid_files)} valid, {len(test_files)} test")
        
        print(f"\nTotal images processed: {total_images}")
        self.create_data_yaml(brands)
    
    def _copy_and_label_images(self, image_files: List[Path], img_dir: Path, label_dir: Path, 
                              class_id: int, brand_name: str):
        """Görselleri kopyala ve YOLO format label'ları oluştur"""
        for img_path in image_files:
            # Görsel dosyasını kopyala
            new_img_name = f"{brand_name}_{img_path.name}"
            new_img_path = img_dir / new_img_name
            shutil.copy2(img_path, new_img_path)
            
            # YOLO format label oluştur (tam görsel için)
            # Format: class_id center_x center_y width height (normalized)
            label_name = new_img_name.replace(img_path.suffix, '.txt')
            label_path = label_dir / label_name
            
            # Basit bir label oluştur - tüm görsel logo olarak kabul et
            with open(label_path, 'w') as f:
                f.write(f"{class_id} 0.5 0.5 0.8 0.8\n")  # Merkezi bbox, %80 coverage
    
    def augment_dataset(self, multiplier: int = 3):
        """Dataset'i data augmentation ile genişlet"""
        print(f"Applying data augmentation with multiplier {multiplier}...")
        
        # Train set için augmentation yap
        train_images_list = list(self.train_images.glob("*.jpg"))
        train_images_list.extend(list(self.train_images.glob("*.png")))
        
        for img_path in train_images_list:
            img = cv2.imread(str(img_path))
            if img is None:
                continue
                
            label_path = self.train_labels / (img_path.stem + '.txt')
            
            for i in range(multiplier):
                # Augmentation uygula
                aug_img = self._apply_augmentation(img)
                
                # Yeni dosya adı
                aug_img_name = f"{img_path.stem}_aug_{i}{img_path.suffix}"
                aug_img_path = self.train_images / aug_img_name
                aug_label_path = self.train_labels / f"{img_path.stem}_aug_{i}.txt"
                
                # Augmented image'ı kaydet
                cv2.imwrite(str(aug_img_path), aug_img)
                
                # Label'ı kopyala (basit augmentation için bbox değişmiyor)
                if label_path.exists():
                    shutil.copy2(label_path, aug_label_path)
        
        print("Data augmentation completed!")
    
    def _apply_augmentation(self, img: np.ndarray) -> np.ndarray:
        """Basit data augmentation uygula"""
        # Rastgele augmentation seç
        aug_type = random.choice(['brightness', 'contrast', 'noise', 'blur', 'flip'])
        
        if aug_type == 'brightness':
            # Parlaklık değiştir
            factor = random.uniform(0.7, 1.3)
            img = cv2.convertScaleAbs(img, alpha=factor, beta=0)
        
        elif aug_type == 'contrast':
            # Kontrast değiştir
            factor = random.uniform(0.8, 1.2)
            img = cv2.convertScaleAbs(img, alpha=factor, beta=0)
        
        elif aug_type == 'noise':
            # Gürültü ekle
            noise = np.random.randint(0, 30, img.shape, dtype=np.uint8)
            img = cv2.add(img, noise)
        
        elif aug_type == 'blur':
            # Hafif blur uygula
            kernel_size = random.choice([3, 5])
            img = cv2.GaussianBlur(img, (kernel_size, kernel_size), 0)
        
        elif aug_type == 'flip':
            # Yatay çevir
            img = cv2.flip(img, 1)
        
        return img
    
    def validate_dataset(self):
        """Dataset'in doğruluğunu kontrol et"""
        print("Validating dataset...")
        
        issues = []
        
        # Her split için kontrol yap
        splits = [
            ('train', self.train_images, self.train_labels),
            ('valid', self.valid_images, self.valid_labels),
            ('test', self.test_images, self.test_labels)
        ]
        
        for split_name, img_dir, label_dir in splits:
            img_files = list(img_dir.glob("*.jpg")) + list(img_dir.glob("*.png"))
            label_files = list(label_dir.glob("*.txt"))
            
            print(f"{split_name}: {len(img_files)} images, {len(label_files)} labels")
            
            # Her görsel için label var mı kontrol et
            for img_file in img_files:
                expected_label = label_dir / (img_file.stem + '.txt')
                if not expected_label.exists():
                    issues.append(f"Missing label for {img_file}")
        
        if issues:
            print(f"Found {len(issues)} issues:")
            for issue in issues[:10]:  # İlk 10 hatayı göster
                print(f"  - {issue}")
        else:
            print("Dataset validation passed!")


def main():
    """Ana fonksiyon - dataset hazırlama"""
    
    # Konfigürasyon
    SOURCE_DATASET = "/path/to/your/raw/car/brand/dataset"  # Ham dataset yolu
    TARGET_DATASET = "/home/fukushima/Desktop/CarBrandDataset"  # Hedef dataset yolu
    
    print("Car Brand Logo Dataset Preparation")
    print("=" * 50)
    
    # Dataset preparator'ı oluştur
    preparator = CarBrandDatasetPreparator(SOURCE_DATASET, TARGET_DATASET)
    
    # Dataset'i böl
    print("Splitting dataset...")
    preparator.split_dataset(train_ratio=0.7, valid_ratio=0.2, test_ratio=0.1)
    
    # Data augmentation (isteğe bağlı)
    apply_augmentation = input("Apply data augmentation? (y/n): ").lower() == 'y'
    if apply_augmentation:
        preparator.augment_dataset(multiplier=2)
    
    # Validation
    preparator.validate_dataset()
    
    print(f"\nDataset preparation completed!")
    print(f"Dataset saved to: {TARGET_DATASET}")
    print("You can now use CarBrandLogoDetection.ipynb for training.")


if __name__ == "__main__":
    main()