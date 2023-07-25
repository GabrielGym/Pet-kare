from rest_framework.views import APIView, Request, Response, status
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from .models import Pet
from .serializers import PetSerializer
from groups.models import Group
from traits.models import Trait
from traits.serializers import TraitSerializer
import ipdb


class PetView(APIView, PageNumberPagination):
    def get(self, request: Request) -> Response:
        pets = Pet.objects.all()

        trait_query = request.query_params.get("trait", None)
        if trait_query:
            pets = Pet.objects.filter(traits__name__iexact=trait_query)

        result_page = self.paginate_queryset(pets, request)
        serializer = PetSerializer(instance=result_page, many=True)

        return self.get_paginated_response(serializer.data)

    def post(self, request: Request) -> Response:
        serializer = PetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        group_data = serializer.validated_data.pop("group")
        traits_data = serializer.validated_data.pop("traits")

        group = Group.objects.filter(
            scientific_name__iexact=group_data["scientific_name"]
        ).first()
        if not group:
            group = Group.objects.create(**group_data)

        pet = Pet.objects.create(**serializer.validated_data, group=group)

        for trait_dict in traits_data:
            trait_obj = Trait.objects.filter(name__iexact=trait_dict["name"]).first()

            if not trait_obj:
                trait_obj = Trait.objects.create(**trait_dict)

            pet.traits.add(trait_obj)

        serializer = PetSerializer(instance=pet)

        return Response(data=serializer.data, status=status.HTTP_201_CREATED)


class PetDetailsView(APIView):
    def get(self, request: Request, pet_id: int) -> Response:
        pet = get_object_or_404(Pet, id=pet_id)
        serializer = PetSerializer(instance=pet)

        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def patch(self, request: Request, pet_id: int) -> Response:
        serializer = PetSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        pet = get_object_or_404(Pet, id=pet_id)

        group_data = serializer.validated_data.pop("group", None)
        traits_data = serializer.validated_data.pop("traits", None)

        if group_data:
            try:
                group = Group.objects.get(scientific_name=group_data["scientific_name"])
            except Group.DoesNotExist:
                group = Group.objects.create(**group_data)
                pet.group = group
            pet.group = group

        if traits_data:
            for trait_data in traits_data:
                try:
                    trait_obj = Trait.objects.get(name=trait_data["name"])
                except Trait.DoesNotExist:
                    trait_obj = Trait.objects.create(**trait_data)
                    pet.traits.add(trait_obj)
                pet.traits.add(trait_obj)

        for key, value in serializer.validated_data.items():
            setattr(pet, key, value)

        pet.save()
        serializer = PetSerializer(instance=pet)

        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def delete(self, request: Request, pet_id: int) -> Response:
        pet = get_object_or_404(Pet, id=pet_id)
        pet.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
