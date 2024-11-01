from rest_framework import serializers
from .models import Cart, CartItem
from products.serializers import ProductSerializer

class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)
    subtotal = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True,
        source='get_subtotal'
    )

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_id', 'quantity', 'subtotal']

    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError("수량은 1개 이상이어야 합니다.")
        return value

    def validate(self, data):
        product_id = data.get('product_id')
        quantity = data.get('quantity', 1)

        # 재고 확인
        from products.models import Product
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            raise serializers.ValidationError("상품이 존재하지 않습니다.")

        if product.stock < quantity:
            raise serializers.ValidationError(f"재고가 부족합니다. 현재 재고: {product.stock}개")

        return data

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True,
        source='get_total_price'
    )

    class Meta:
        model = Cart
        fields = ['id', 'items', 'total_price', 'created_at', 'updated_at']