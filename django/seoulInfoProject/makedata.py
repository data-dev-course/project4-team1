from info_app.models import Place

pname = "충정로역"
ppopulation = "혼잡"
pclass = "인구밀집지역"

for i in range(11, 100):
    q = Place(name=pname + str(i), population=ppopulation, place_class=pclass)
    q.save()
# test
Place.objects.all()
