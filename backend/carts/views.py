from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer
from products.models import Product

class CartViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = CartSerializer

    def get_queryset(self):
        # 사용자의 장바구니 조회
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        return Cart.objects.filter(id=cart.id)

    def get_object(self):
        # 현재 사용자의 장바구니 반환
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        return cart

    @action(detail=True, methods=['post'])
    def add_item(self, request, pk=None):
        cart = self.get_object()
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))

        try:
            product = Product.objects.get(id=product_id)

            # 재고 확인
            if product.stock < quantity:
                return Response(
                    {"error": f"재고가 부족합니다. 현재 재고: {product.stock}개"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # 장바구니에 이미 있는 상품인지 확인
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                product=product,
                defaults={'quantity': quantity}
            )

            if not created:
                # 기존 수량에 추가
                cart_item.quantity += quantity
                if cart_item.quantity > product.stock:
                    return Response(
                        {"error": f"재고가 부족합니다. 현재 재고: {product.stock}개"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                cart_item.save()

            serializer = CartItemSerializer(cart_item)
            return Response(serializer.data)

        except Product.DoesNotExist:
            return Response(
                {"error": "상품이 존재하지 않습니다."},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'])
    def remove_item(self, request, pk=None):
        cart = self.get_object()
        product_id = request.data.get('product_id')

        try:
            cart_item = CartItem.objects.get(
                cart=cart,
                product_id=product_id
            )
            cart_item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        except CartItem.DoesNotExist:
            return Response(
                {"error": "장바구니에 해당 상품이 없습니다."},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'])
    def update_quantity(self, request, pk=None):
        cart = self.get_object()
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))

        try:
            cart_item = CartItem.objects.get(
                cart=cart,
                product_id=product_id
            )

            # 재고 확인
            if cart_item.product.stock < quantity:
                return Response(
                    {"error": f"재고가 부족합니다. 현재 재고: {cart_item.product.stock}개"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            cart_item.quantity = quantity
            cart_item.save()

            serializer = CartItemSerializer(cart_item)
            return Response(serializer.data)

        except CartItem.DoesNotExist:
            return Response(
                {"error": "장바구니에 해당 상품이 없습니다."},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'])
    def clear(self, request, pk=None):
        cart = self.get_object()
        cart.items.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)